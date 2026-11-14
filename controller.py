
import time
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3

class BackupController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(BackupController, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.down_ports = set()
        self.active_path = None
        self.last_link_down_time = None

        self.paths = {
            "primary": {
                1: (1, 2),
                2: (1, 2),
                4: (1, 3)
            },
            "backup": {
                1: (1, 3),
                3: (1, 2),
                4: (2, 3)
            }
        }

        self.path_ports = {
            "primary": {(1, 2), (2, 1), (2, 2), (4, 1)},
            "backup": {(1, 3), (3, 1), (3, 2), (4, 2)}
        }

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        dp = ev.msg.datapath
        self.datapaths[dp.id] = dp
        self.logger.info("Switch connected: %s", dp.id)

        if len(self.datapaths) == 4:
            self.update_paths()

    def install_flow(self, dp, in_port, out_port):
        parser = dp.ofproto_parser
        ofp = dp.ofproto
        match = parser.OFPMatch(in_port=in_port)
        actions = [parser.OFPActionOutput(out_port)]
        instructions = [
            parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)
        ]
        mod = parser.OFPFlowMod(
            datapath=dp,
            priority=100,
            match=match,
            instructions=instructions
        )
        dp.send_msg(mod)

    def update_paths(self):
        if self.path_ports["primary"].isdisjoint(self.down_ports):
            selected = "primary"
        elif self.path_ports["backup"].isdisjoint(self.down_ports):
            selected = "backup"
        else:
            self.logger.warning("Both paths are unavailable!")
            return

        if selected == self.active_path:
            return

        for dp in self.datapaths.values():
            parser = dp.ofproto_parser
            ofp = dp.ofproto
            mod = parser.OFPFlowMod(
                datapath=dp,
                command=ofp.OFPFC_DELETE,
                table_id=0,
                out_port=ofp.OFPP_ANY,
                out_group=ofp.OFPG_ANY,
                match=parser.OFPMatch()
            )
            dp.send_msg(mod)

        for dpid, (forward_in, forward_out) in self.paths[selected].items():
            dp = self.datapaths.get(dpid)
            if dp is None:
                continue

            self.install_flow(dp, forward_in, forward_out)

            reverse_in, reverse_out = forward_out, forward_in
            self.install_flow(dp, reverse_in, reverse_out)

        self.active_path = selected
        self.logger.info("ACTIVE PATH: %s", selected.upper())

        if self.last_link_down_time is not None:
            recovery_time = time.perf_counter() - self.last_link_down_time
            self.logger.info(
                "SDN FAILOVER REACTION TIME: %.6f seconds",
                recovery_time
            )
            self.last_link_down_time = None

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_status_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        port = msg.desc.port_no
        key = (dp.id, port)

        if msg.desc.state & dp.ofproto.OFPPS_LINK_DOWN:
            self.down_ports.add(key)

            if self.last_link_down_time is None:
                self.last_link_down_time = time.perf_counter()

            self.logger.warning(
                "LINK DOWN: switch %s port %s", dp.id, port
            )
        else:
            self.down_ports.discard(key)
            self.logger.info(
                "LINK UP: switch %s port %s", dp.id, port
            )

        self.update_paths()
