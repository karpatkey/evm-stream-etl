# MIT License
#
# Copyright (c) 2018 Evgeniy Filatov, evgeniyfilatov@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from ethereumetl.domain.internal_transaction import ETHInternalTransaction
from ethereumetl.mainnet_daofork_state_changes import DAOFORK_BLOCK_NUMBER
from ethereumetl.utils import hex_to_dec, to_normalized_address


class EthInternalTransactionMapper(object):
    def json_dict_to_internal_transaction(self, json_dict):
        
        internal_transaction = ETHInternalTransaction()
        
        internal_transaction.block_number = json_dict.get('blockNumber')
        internal_transaction.transaction_hash = json_dict.get('transactionHash')
        error = json_dict.get('error')

        if error:
            internal_transaction.error = error

        action = json_dict.get('action')
        if action is None:
            action = {}
        result = json_dict.get('result')
        if result is None:
            result = {}

        trace_type = json_dict.get('type')
        trace_value = json_dict.get('value')
        internal_transaction.trace_type = trace_type

        # common fields in call/create
        if trace_type in ('call') and trace_value>0:
            internal_transaction.value = trace_value
            return internal_transaction
        
        else: 
            return None
        
    def internal_transaction_to_dict(self, internal_transaction):
        return {
            
            'type': 'internal_transaction',
            'block_number': internal_transaction.block_number,
            'transaction_hash': internal_transaction.transaction_hash,
            'from_address': internal_transaction.from_address,
            'to_address': internal_transaction.to_address,
            'value': internal_transaction.value,
            'index':internal_transaction.index
        }


    # def geth_trace_to_traces(self, geth_trace):
    #     block_number = geth_trace.block_number
    #     transaction_traces = geth_trace.transaction_traces

    #     traces = []

    #     for tx_index, tx_trace in enumerate(transaction_traces):
    #         traces.extend(self._iterate_transaction_trace(
    #             block_number,
    #             tx_index,
    #             tx_trace,
    #         ))

    #     return traces

    # def genesis_alloc_to_trace(self, allocation):
    #     address = allocation[0]
    #     value = allocation[1]

    #     trace = EthTrace()

    #     trace.block_number = 0
    #     trace.to_address = address
    #     trace.value = value
    #     trace.trace_type = 'genesis'
    #     trace.status = 1

    #     return trace

    # def daofork_state_change_to_trace(self, state_change):
    #     from_address = state_change[0]
    #     to_address = state_change[1]
    #     value = state_change[2]

    #     trace = EthTrace()

    #     trace.block_number = DAOFORK_BLOCK_NUMBER
    #     trace.from_address = from_address
    #     trace.to_address = to_address
    #     trace.value = value
    #     trace.trace_type = 'daofork'
    #     trace.status = 1

    #     return trace

    # def _iterate_transaction_trace(self, block_number, tx_index, tx_trace, trace_address=[]):
    #     trace = EthTrace()

    #     trace.block_number = block_number
    #     trace.transaction_index = tx_index

    #     trace.from_address = to_normalized_address(tx_trace.get('from'))
    #     trace.to_address = to_normalized_address(tx_trace.get('to'))

    #     trace.input = tx_trace.get('input')
    #     trace.output = tx_trace.get('output')

    #     trace.value = hex_to_dec(tx_trace.get('value'))
    #     trace.gas = hex_to_dec(tx_trace.get('gas'))
    #     trace.gas_used = hex_to_dec(tx_trace.get('gasUsed'))

    #     trace.error = tx_trace.get('error')

    #     # lowercase for compatibility with parity traces
    #     trace.trace_type = tx_trace.get('type').lower()

    #     if trace.trace_type == 'selfdestruct':
    #         # rename to suicide for compatibility with parity traces
    #         trace.trace_type = 'suicide'
    #     elif trace.trace_type in ('call', 'callcode', 'delegatecall', 'staticcall'):
    #         trace.call_type = trace.trace_type
    #         trace.trace_type = 'call'

    #     result = [trace]

    #     calls = tx_trace.get('calls', [])

    #     trace.subtraces = len(calls)
    #     trace.trace_address = trace_address

    #     for call_index, call_trace in enumerate(calls):
    #         result.extend(self._iterate_transaction_trace(
    #             block_number,
    #             tx_index,
    #             call_trace,
    #             trace_address + [call_index]
    #         ))

    #     return result


