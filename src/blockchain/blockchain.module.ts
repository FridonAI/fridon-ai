import { Module } from '@nestjs/common';
import { Connection } from '@solana/web3.js';
import { connection } from './utils/connection';
import { BlockchainController } from './blockchain.controller';
import { BlockchainService } from './blockchain.service';
import { BlockchainTools } from './utils/tools/token-list';

@Module({
  controllers: [BlockchainController],
  providers: [
    BlockchainService,
    BlockchainTools,
    {
      provide: Connection,
      useValue: connection,
    },
  ],
})
export class BlockchainModule {}
