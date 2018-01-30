REGISTER_TARGET_COMM_TARGET_NAME = 'register_target'


def configure_comm(comm, comm_id, msg_callback):
    comm.comm_id = comm_id
    comm.on_msg(msg_callback)


def register_target_comm_open(comm, open_msg):
    # Register a new comm target.
    def msg_callback(msg):
        data = msg['content']['data']
        comm.kernel.comm_manager.register_target(
            target_name=data['new_target_name'],
            f=data['comm_open_callback']
        )
    configure_comm(comm, comm_id='', msg_callback=msg_callback)
