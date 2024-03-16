import { Module } from '@nestjs/common';
import { ChatModule } from './chat/chat.module';
import { EventsModule } from './events/events.module';
import { AuthModule } from './auth/auth.module';
import { BlockchainModule } from './blockchain/blockchain.module';
import { ConfigModule } from '@nestjs/config';
import {
  PrismaModule,
  providePrismaClientExceptionFilter,
} from 'nestjs-prisma';

@Module({
  imports: [
    // Nest Modules
    ConfigModule.forRoot({ isGlobal: true }),
    PrismaModule.forRoot({ isGlobal: true }),
    // Custom Modules
    AuthModule,
    ChatModule,
    EventsModule,
    BlockchainModule,
  ],
  providers: [providePrismaClientExceptionFilter()],
})
export class AppModule {}
