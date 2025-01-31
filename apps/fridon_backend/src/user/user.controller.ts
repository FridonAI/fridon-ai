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
import { PaymentBodyDto, UserPluginsResponseDto } from './user.dto';
import { ApiSecurity, ApiTags } from '@nestjs/swagger';
import { UserService } from './user.service';
import { PluginsService } from 'src/plugins/plugins.service';
import { Auth, Role } from 'src/auth/decorators/auth.decorator';
import { Claims } from 'src/auth/decorators/claims.decorator';

@ApiTags('user')
@Controller('user')
export class UserController {
  private readonly logger = new Logger(UserController.name);

  constructor(
    private readonly transactionListenerService: TransactionListenerService,
    private readonly userService: UserService,
    private readonly pluginsService: PluginsService,
  ) {}

  // todo: remove it later. after generating beta key-pair.
  // @Get('/test')
  // async test() {
  //   const keypair = Keypair.generate();

  //   console.log(Buffer.from(keypair.secretKey).toString("hex")  );
  //   // Extract public and secret keys
  //   const publicKey = keypair.publicKey.toBase58();
  //   const secretKey = Buffer.from(keypair.secretKey).toString("base64");

  //   console.log("Public Key (PK):", publicKey);
  //   console.log("Secret Key (SK) - Base64 Encoded:", secretKey);
  //   JSON.stringify(Array.from(keypair.secretKey));

  // }

  @Post('/purchase')
  @ApiSecurity('auth')
  @Auth(Role.User)
  async processPaymentTransaction(
    @Claims('sub') walletAddress: string,
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
        walletId: walletAddress,
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
        walletId: walletAddress,
        chatId: 'NaN',
        personality: 'NaN',
        plugin: body.pluginId,
      },
    );
  }

  @Get('/me/plugins')
  @ApiSecurity('auth')
  @Auth(Role.User)
  async getPlugins(
    @Claims('sub') walletAddress: string,
  ): Promise<UserPluginsResponseDto> {
    const pluginList = await this.userService.getUserPlugins(walletAddress);

    const purchaseInProgressPlugins =
      await this.transactionListenerService.getPurchaseInProgressPlugins(
        walletAddress,
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
