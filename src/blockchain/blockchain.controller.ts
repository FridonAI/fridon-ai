import { Controller, Get } from '@nestjs/common';
import { BlockchainService } from './blockchain.service';
import { ApiTags } from '@nestjs/swagger';

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
}
