import { Module } from '@nestjs/common';
import { ChatModule } from './chat/chat.module';
import { EventsModule } from './events/events.module';
import { AuthModule } from './auth/auth.module';
import { BlockchainModule } from './blockchain/blockchain.module';

@Module({
  imports: [AuthModule, ChatModule, EventsModule, BlockchainModule],
})
export class AppModule {}
