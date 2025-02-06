import {
  BadRequestException,
  Body,
  Controller,
  Get,
  Logger,
  NotFoundException,
  Post,
} from '@nestjs/common';
import { TransactionListenerService } from 'src/blockchain/transaction-listener/transaction-listener.service';
import { TransactionType } from 'src/blockchain/transaction-listener/types';
import {
  PaymentBodyDto,
  UserPluginsResponseDto,
  VerifyBodyDto,
} from './user.dto';
import { ApiTags } from '@nestjs/swagger';
import { Auth, Wallet, WalletSession } from '@lib/auth';
import { UserService } from './user.service';
import { PluginsService } from 'src/plugins/plugins.service';

@ApiTags('user')
@Controller('user')
@Auth()
export class UserController {
  private readonly logger = new Logger(UserController.name);

  constructor(
    private readonly transactionListenerService: TransactionListenerService,
    private readonly userService: UserService,
    private readonly pluginsService: PluginsService,
  ) {}

  @Get('/verify')
  async getWalletVerification(@Wallet() wallet: WalletSession) {
    const userData = await this.userService.getWalletVerification(
      wallet.walletAddress,
    );

    return {
      walletId: wallet.walletAddress,
      verified: userData?.verified ?? false,
    };
  }

  @Post('/verify')
  /**
   * Verify a transaction and make user **Verified**.
   * Steps to produce:
   * 1. Register transaction inside the queue.
   * 2. Validate transaction receiver and amount.
   * 3. Update user(Sender) status to **Verified**.
   */
  async verifyTransaction(
    @Wallet() wallet: WalletSession,
    @Body() body: VerifyBodyDto,
  ) {
    const { verified } = await this.getWalletVerification(wallet);

    if (verified) {
      throw new BadRequestException('User already verified');
    }

    await this.transactionListenerService.registerTransactionListener(
      body.transactionId,
      TransactionType.VERIFY,
      {
        walletId: wallet.walletAddress,
        chatId: 'NaN',
        personality: 'NaN',
      },
    );
  }

  @Post('/purchase')
  async processPaymentTransaction(
    @Wallet() wallet: WalletSession,
    @Body() body: PaymentBodyDto,
  ) {
    const plugin = this.pluginsService.get(body.pluginId);
    if (!plugin) {
      throw new NotFoundException(`Plugin[${body.pluginId}] not found`);
    }

    console.log(plugin.price, plugin.price === 0, 0);
    if (plugin.price === 0) {
      // free plugin
      this.logger.debug(`Purchasing Free Plugin[${plugin.name}]`);
      const expirationDate = new Date();
      expirationDate.setMonth(expirationDate.getMonth() + 1);

      await this.userService.assignPlugin({
        walletId: wallet.walletAddress,
        pluginId: plugin.slug,
        expiresAt: expirationDate,
      });
      return;
    }

    if (!body.transactionId) {
      throw new BadRequestException('Transaction is required for paid plugins');
    }

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
