import { Module } from '@nestjs/common';
import { Connection } from '@solana/web3.js';
import { BlockchainController } from './blockchain.controller';
import { BlockchainService } from './blockchain.service';

@Module({
  providers: [
    BlockchainService,
    {
      provide: Connection,
      useValue: new Connection('https://api.devnet.solana.com'),
    },
  ],
  controllers: [BlockchainController],
})
export class BlockchainModule {}
