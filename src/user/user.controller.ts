import { Body, Controller, Get, Post } from '@nestjs/common';
import { TransactionListenerService } from 'src/blockchain/transaction-listener/transaction-listener.service';
import { TransactionType } from 'src/blockchain/transaction-listener/types';
import { PaymentBodyDto, UserPluginsResponseDto } from './user.dto';
import { ApiTags } from '@nestjs/swagger';
import { Auth, Wallet, WalletSession } from '@lib/auth';
import { UserService } from './user.service';

@ApiTags('user')
@Controller('user')
@Auth()
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
        plugin: body.pluginId,
      },
    );
  }

  @Get('/me/plugins')
  async getPlugins(
    @Wallet() wallet: WalletSession,
  ): Promise<UserPluginsResponseDto> {
    const pluginList = await this.userService.getUserPlugins(
      wallet.walletAddress,
    );

    const purchaseInProgressPlugins =
      await this.transactionListenerService.getPurchaseInProgressPlugins(
        wallet.walletAddress,
      );

    return {
      plugins: [
        ...pluginList.map((plugin) => ({
          id: plugin.id,
          type: 'Purchased' as const,
          expiresAt: plugin.expiresAt?.toISOString() ?? null,
        })),
        ...purchaseInProgressPlugins
          .map((plugin) => ({
            id: plugin,
            type: 'PurchaseInProgress' as const,
            expiresAt: null,
          }))
          .filter((plugin) => !pluginList.some((p) => p.id === plugin.id)),
      ],
    };
  }
}
