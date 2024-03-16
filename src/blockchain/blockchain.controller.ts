import { Body, Controller, Get, Post } from '@nestjs/common';
import { BlockchainService } from './blockchain.service';
import { ApiTags } from '@nestjs/swagger';
import { TransferTokenDto } from './blockchain.dto';

@Controller('blockchain')
@ApiTags('blockchain')
export class BlockchainController {
  constructor(readonly blockchainService: BlockchainService) {}

  @Get('latest-block-hash')
  async getLatestsBlockHash(): Promise<{ blockHash: string }> {
    return {
      blockHash: await this.blockchainService.getLatestsBlockHash(),
    };
  }

  @Post('create-token-account')
  async createTokenAccount(): Promise<{ tokenAccount: string }> {
    return {
      tokenAccount: await this.blockchainService.createTokenAccount(),
    };
  }

  @Post('transfer-tokens')
  async transferTokens(
    @Body() body: TransferTokenDto,
  ): Promise<{ transfered: boolean }> {
    return {
      transfered: await this.blockchainService.transferTokens(
        body.walletAddress,
        body.toAddress,
        body.mintAddress,
        body.amount,
      ),
    };
  }
}
