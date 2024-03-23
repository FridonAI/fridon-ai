import { Module } from '@nestjs/common';
import { Connection } from '@solana/web3.js';
import { connection } from './utils/connection';
import { BlockchainController } from './blockchain.controller';
import { BlockchainService } from './blockchain.service';
import { BlockchainTools } from './utils/tools/token-list';
import { KaminoFactory } from './factories/kamino-factory';
import { TokenProgramInstructionFactory } from './factories/token-program-instruction-factory';
import { TokenProgramTransactionFactory } from './factories/token-program-transaction-factory';
import { TransactionFactory } from './factories/transaction-factory';
import { BullModule } from '@nestjs/bullmq';
import { TRANSACTION_LISTENER_QUEUE } from './transaction-listener/types';
import { TransactionListenerProcessor } from './transaction-listener/transaction-listener.processor';
import { TransactionListenerService } from './transaction-listener/transaction-listener.service';

@Module({
  imports: [BullModule.registerQueue({ name: TRANSACTION_LISTENER_QUEUE })],
  controllers: [BlockchainController],
  providers: [
    BlockchainService,
    BlockchainTools,
    {
      provide: Connection,
      useValue: connection,
    },
    KaminoFactory,
    TokenProgramInstructionFactory,
    TokenProgramTransactionFactory,
    TransactionFactory,
    TransactionListenerProcessor,
    TransactionListenerService,
  ],
  exports: [TransactionFactory, TransactionListenerService],
})
export class BlockchainModule {
  static forRoot() {
    return {
      module: BlockchainModule,
      global: true,
    };
  }
}
