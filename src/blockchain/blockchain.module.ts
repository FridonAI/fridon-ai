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

@Module({
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
  ],
})
export class BlockchainModule {}
