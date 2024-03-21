import { Body, Controller, Post } from '@nestjs/common';
import { ApiTags } from '@nestjs/swagger';
import {
  TransferTokenResponseDto,
  TransferTokenRequestBodyDto,
  DefiOperationRequestBodyDto,
  DefiOperationResponseBodyDto,
} from './blockchain.dto';
import { BlockchainService } from './blockchain.service';

@Controller('blockchain')
@ApiTags('blockchain')
export class BlockchainController {
  constructor(readonly blockchainService: BlockchainService) {}

  @Post('transfer-tokens')
  async transferTokens(
    @Body() body: TransferTokenRequestBodyDto,
  ): Promise<TransferTokenResponseDto> {
    const serializedTx = await this.blockchainService.transferTokens(
      body.walletAddress,
      body.toAddress,
      body.currency,
      body.amount,
    );

    return new TransferTokenResponseDto({
      status: true,
      message: 'Success',
      data: {
        serializedTx,
      },
    });
  }

  // Provider Transaction Operations
  @Post('defi-operation')
  async defiOperations(
    @Body() body: DefiOperationRequestBodyDto,
  ): Promise<DefiOperationResponseBodyDto> {
    const serializedTx = await this.blockchainService.defiOperations(
      body.walletAddress,
      body.operation,
      body.provider,
      body.currency,
      body.amount,
    );

    return new TransferTokenResponseDto({
      status: true,
      message: 'Success',
      data: {
        serializedTx,
      },
    });
  }
}
