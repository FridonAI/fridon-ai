import { Module } from '@nestjs/common';
import { Connection } from '@solana/web3.js';
import { connection } from './utils/connection';
import { BlockchainController } from './blockchain.controller';
import { BlockchainService } from './blockchain.service';
import { BlockchainTools } from './utils/tools/blockchain-tools';
import { KaminoFactory } from './providers/kamino-factory';
import { TokenProgramInstructionFactory } from './factories/token-program-instruction-factory';
import { TokenProgramTransactionFactory } from './factories/token-program-transaction-factory';
import { TransactionFactory } from './factories/transaction-factory';
import { BullModule } from '@nestjs/bullmq';
import { TRANSACTION_LISTENER_QUEUE } from './transaction-listener/types';
import { TransactionListenerProcessor } from './transaction-listener/transaction-listener.processor';
import { TransactionListenerService } from './transaction-listener/transaction-listener.service';
import { NumberFormatter } from './utils/tools/number-formatter';
import { WalletFactory } from './providers/wallet-factory';
import { SymmetryApiFactory } from './providers/symmetry-api-factory';
import { PointsFactory } from './providers/points-factory';
import { JupiterFactory } from './providers/jupiter-factory';
import { GetBlockHash } from 'src/data-providers/actions/get-blockhash';
import { UpdateTokenList } from './cron/update-token-list.cron';
import { UpdateKaminoReserve } from './cron/update-kamino-reserve.cron';
import { UpdateCoinPrices } from './cron/update-coin-prices.cron';

@Module({
  imports: [
    BullModule.registerQueue({ name: TRANSACTION_LISTENER_QUEUE }),
  ],
  controllers: [BlockchainController],
  providers: [
    BlockchainService,
    BlockchainTools,
    NumberFormatter,
    {
      provide: Connection,
      useValue: connection,
    },
    KaminoFactory,
    JupiterFactory,
    PointsFactory,
    SymmetryApiFactory,
    WalletFactory,
    TokenProgramInstructionFactory,
    TokenProgramTransactionFactory,
    TransactionFactory,
    TransactionListenerProcessor,
    TransactionListenerService,
    GetBlockHash,
    UpdateTokenList,
    UpdateKaminoReserve,
    UpdateCoinPrices,
  ],
  exports: [
    TransactionFactory,
    TransactionListenerService,
    Connection,
    BlockchainTools,
    TokenProgramInstructionFactory,
    TokenProgramTransactionFactory,
    TransactionFactory,
    KaminoFactory,
    JupiterFactory,
    PointsFactory,
    SymmetryApiFactory,
    WalletFactory,
  ],
})
export class BlockchainModule {
  static forRoot() {
    return {
      module: BlockchainModule,
      global: true,
    };
  }
}
