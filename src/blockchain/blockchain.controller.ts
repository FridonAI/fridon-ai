import { Body, Controller, Post } from '@nestjs/common';
import { ApiTags } from '@nestjs/swagger';
import {
  TransferTokenResponseDto,
  TransferTokenRequestBodyDto,
  DefiOperationRequestBodyDto,
  DefiOperationResponseDto,
  BalanceOperationRequestBodyDto,
  BalanceOperationResponseDto,
  PointsRequestBodyDto,
  PointsResponseDto,
  // BalanceOperationResponseBodyDto,
} from './blockchain.dto';
import { BlockchainService } from './blockchain.service';
import { TransactionFactory } from './factories/transaction-factory';
import { Connection } from '@solana/web3.js';
import { Logger } from '@nestjs/common';

@Controller('blockchain')
@ApiTags('blockchain')
export class BlockchainController {
  private logger = new Logger(BlockchainController.name);

  constructor(
    readonly connection: Connection,
    readonly blockchainService: BlockchainService,
    readonly transactionFactory: TransactionFactory,
  ) {}

  @Post('transfer-tokens')
  async transferTokens(
    @Body() body: TransferTokenRequestBodyDto,
  ): Promise<TransferTokenResponseDto> {
    this.logger.debug('Body', JSON.stringify(body, null, 2));
    const serializedTx = await this.blockchainService.transferTokens(
      body.walletAddress,
      body.toAddress,
      body.currency,
      body.amount,
    );

    return new TransferTokenResponseDto({
      data: {
        serializedTx: Object.values(serializedTx),
      },
    });
  }

  // Provider Transaction Operations
  @Post('defi-operation')
  async defiOperations(
    @Body() body: DefiOperationRequestBodyDto,
  ): Promise<DefiOperationResponseDto> {
    this.logger.debug('Body', JSON.stringify(body, null, 2));
    const tx = await this.blockchainService.defiOperations(
      body.walletAddress,
      body.operation,
      body.provider,
      body.currency,
      body.amount,
    );

    // Sign Message

    // // Send transaction
    // const txId = await this.transactionFactory.sendSerializedTransaction(
    //   this.connection,
    //   signedSerializedTx.serialize(),
    // );

    // console.log('txId', txId);
    return new TransferTokenResponseDto({
      data: {
        serializedTx: Object.values(tx.serialize()),
      },
    });
  }

  @Post('balance-operation')
  async balanceOperations(
    @Body() body: BalanceOperationRequestBodyDto,
  ): Promise<BalanceOperationResponseDto> {
    this.logger.debug('Body', JSON.stringify(body, null, 2));
    const balances = await this.blockchainService.balanceOperations(
      body.walletAddress,
      body.provider,
      body.operation,
      body.currency,
    );

    return new BalanceOperationResponseDto({
      data: balances,
    });
  }

  @Post('symmetry/baskets')
  async getSymmetryInformation() {
    const result = await this.blockchainService.getSymmetryBaskets();

    // todo: write paginations and response DTO.
    return result;
  }

  @Post('points')
  async getProtocolPoints(@Body() body: PointsRequestBodyDto) {
    const result = await this.blockchainService.getProtocolPoints(
      body.walletAddress,
      body.provider,
    );

    return new PointsResponseDto({
      data: result,
    });
  }
}
