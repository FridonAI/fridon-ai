import { Body, Controller, Get, Post } from '@nestjs/common';
import { TransactionListenerService } from 'src/blockchain/transaction-listener/transaction-listener.service';
import { TransactionType } from 'src/blockchain/transaction-listener/types';
import { PaymentBodyDto } from './user.dto';
import { ApiTags } from '@nestjs/swagger';
import { Wallet, WalletSession } from '@lib/auth';
import { UserService } from './user.service';

@ApiTags('user')
@Controller('user')
export class UserController {
  constructor(
    private readonly transactionListenerService: TransactionListenerService,
    private readonly userService: UserService,
  ) {}

  @Post('/purchase')
  async processPaymentTransaction(
    @Wallet() wallet: WalletSession,
    @Body() body: PaymentBodyDto,
  ) {
    await this.transactionListenerService.registerTransactionListener(
      body.transactionId,
      TransactionType.PAYMENT,
      {
        walletId: wallet.walletAddress,
        chatId: 'NaN',
        personality: 'NaN',
        plugin: body.plugin,
      },
    );
  }

  @Get('/me/plugins')
  async getPlugins(@Wallet() wallet: WalletSession) {
    return this.userService.getUserPlugins(wallet.walletAddress);
  }
}
