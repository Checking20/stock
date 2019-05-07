from bert_serving.server.helper import get_args_parser
from bert_serving.server import BertServer

args = get_args_parser().parse_args(['-model_dir', 'BertModel',
                                     '-port', '5555',
                                     '-port_out', '5556',
                                     '-max_seq_len', 'NONE',
                                     '-cpu'])
server = BertServer(args)
server.start()