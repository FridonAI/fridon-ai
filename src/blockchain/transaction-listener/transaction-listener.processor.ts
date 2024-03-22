import { Processor, WorkerHost } from '@nestjs/bullmq';
import { TRANSACTION_LISTENER_QUEUE, TransactionListenerJob } from './types';

@Processor(TRANSACTION_LISTENER_QUEUE)
export class TransactionListenerProcessor extends WorkerHost {
  async process(job: TransactionListenerJob): Promise<any> {
    console.log('Processing job', job.id, job.data);
  }
}
