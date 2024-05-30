import { Body, Controller, Post } from '@nestjs/common';
import { TransactionListenerService } from 'src/blockchain/transaction-listener/transaction-listener.service';
import { TransactionType } from 'src/blockchain/transaction-listener/types';
import { PaymentBodyDto } from './user.dto';
import { ApiTags } from '@nestjs/swagger';

@ApiTags('user')
@Controller('user')
export class UserController {
  constructor(
    private readonly transactionListenerService: TransactionListenerService,
  ) {}

  @Post('/purchase')
  async processPaymentTransaction(@Body() body: PaymentBodyDto) {
    await this.transactionListenerService.registerTransactionListener(
      body.transactionId,
      TransactionType.PAYMENT,
      { chatId: 'NaN', personality: 'NaN' },
    );
  }
}
