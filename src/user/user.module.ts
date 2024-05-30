import { Module } from '@nestjs/common';
import { UserService } from './user.service';
import { UserController } from './user.controller';
import {
  TransactionConfirmedHandler,
  TransactionSkippedHandler,
  TransactionFailedHandler,
} from './event-handlers/blockchain.evet-handlers';

@Module({
  controllers: [UserController],
  providers: [
    UserService,
    TransactionConfirmedHandler,
    TransactionSkippedHandler,
    TransactionFailedHandler,
  ],
})
export class UserModule {}
