import { Global, Module } from '@nestjs/common';
import { UserService } from './user.service';
import { UserController } from './user.controller';
import {
  PurchaseTransactionConfirmedHandler,
  TransactionSkippedHandler,
  TransactionFailedHandler,
} from './event-handlers/blockchain.evet-handlers';

@Global()
@Module({
  controllers: [UserController],
  providers: [
    UserService,
    PurchaseTransactionConfirmedHandler,
    TransactionSkippedHandler,
    TransactionFailedHandler,
  ],
  exports: [UserService],
})
export class UserModule {}
