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
import logging

from blockchainetl.jobs.base_job import BaseJob
from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from ethereumetl.mainnet_daofork_state_changes import DAOFORK_BLOCK_NUMBER
from ethereumetl.mappers.internal_transactions_mapper import \
    EthInternalTransactionMapper
from ethereumetl.service.eth_special_trace_service import \
    EthSpecialTraceService
from ethereumetl.utils import validate_range


class ExportInternalTransactionsJob(BaseJob):
    def __init__(
            self,
            start_block,
            end_block,
            batch_size,
            web3,
            item_exporter,
            max_workers,
            include_genesis_traces=False,
            include_daofork_traces=False):
        validate_range(start_block, end_block)
        self.start_block = start_block
        self.end_block = end_block

        self.web3 = web3

        self.batch_work_executor = BatchWorkExecutor(1, max_workers)
        self.item_exporter = item_exporter
        
        self.internal_transction_mapper = EthInternalTransactionMapper()

        #TODO Migrate this special case of genesis and daofork traces: 
        self.special_trace_service = EthSpecialTraceService()
        self.include_genesis_traces = include_genesis_traces
        self.include_daofork_traces = include_daofork_traces

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        self.batch_work_executor.execute(
            range(self.start_block, self.end_block + 1),
            self._export_batch,
            total_items=self.end_block - self.start_block + 1
        )

    def _export_batch(self, block_number_batch):
        assert len(block_number_batch) == 1
        logging.info('Exporting internal transactions for block_number=%s', block_number_batch)
        block_number = block_number_batch[0]

        all_traces = []

        #TODO Migrate this special case of genesis and daofork traces: 
        if self.include_genesis_traces and 0 in block_number_batch:
            genesis_traces = self.special_trace_service.get_genesis_traces()
            all_traces.extend(genesis_traces)

        if self.include_daofork_traces and DAOFORK_BLOCK_NUMBER in block_number_batch:
            daofork_traces = self.special_trace_service.get_daofork_traces()
            all_traces.extend(daofork_traces)


        # json_traces = self.web3.parity.traceBlock(block_number)
        
        # debug trace block by number call to the node, tested and available for nodes. 
        # block_number=242191083
        block = hex(block_number)

        #ByNumber
        json_traces = self.web3.provider.make_request("debug_traceBlockByNumber", [block, {"tracer": "callTracer"}]).get('result')

        if json_traces is None:
            raise ValueError('Response from the node is None. Is the node fully synced? Is the node started with tracing enabled? Is trace_block API enabled?')
        traces = [self.internal_transction_mapper.json_dict_to_internal_transaction(json_trace) for json_trace in json_traces]
        #filter none values (traces but not internal transactions) and add block number to the internal transactions
        traces = [
            trace for trace in traces if trace is not None
        ]

        for trace in traces:
            trace.block_number = block_number

        all_traces.extend(traces)


        for trace in all_traces:
            self.item_exporter.export_item(self.internal_transction_mapper.internal_transaction_to_dict(trace))

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()


def calculate_interna_transaction_indexes(internal_transactions):
    # Only works if traces were originally ordered correctly which is the case for Parity traces
    for ind, internal_transaction in enumerate(internal_transactions):
        internal_transaction.index = ind
