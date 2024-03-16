import { Module } from '@nestjs/common';
import { Connection } from '@solana/web3.js';
import { BlockchainController } from './blockchain.controller';
import { BlockchainService } from './blockchain.service';
import { connection } from './utils/connection';

@Module({
  providers: [
    BlockchainService,
    {
      provide: Connection,
      useValue: connection,
    },
  ],
  controllers: [BlockchainController],
})
export class BlockchainModule {}
