import { BadRequestException, Injectable } from '@nestjs/common';
import { Connection } from '@solana/web3.js';

import { RegistryService } from './registry';

@Injectable()
export class DataProviderService {
  constructor(
    private connection: Connection,
    private registryService: RegistryService,
  ) {}

  async resolve(action: string, body: object): Promise<object> {
    const cls = this.registryService.resolve(action);

    if (!cls) {
      throw new BadRequestException(`No function found for action: ${action}`);
    }

    const instance = new cls(this.connection);

    return await instance.execute(body);
  }
}
