import { BadRequestException, Injectable } from '@nestjs/common';
import getBlockHash from './actions/get-blockhash';
import { Connection } from '@solana/web3.js';

type DynamicFnType = (data: any, helpers: Helpers) => Promise<any>;

export type Helpers = {
  connection: Connection;
};

@Injectable()
export class DataProviderService {
  constructor(private connection: Connection) {}
  // async resolve(action: string): Promise<DynamicFnType> {
  //   try {
  //     const actionModulePath = join('./actions', `${action}`);
  //     console.log('actionModulePath', actionModulePath);
  //     const actionModule = await import(actionModulePath);
  //     return actionModule.default;
  //   } catch (error) {
  //     throw new Error(`No function found for action: ${action}`);
  //   }
  // }

  async resolve(action: string, body: object): Promise<object> {
    const fns: Record<string, DynamicFnType> = {
      'get-blockhash': getBlockHash,
    };

    const fn = fns[action];
    if (!fn) {
      throw new BadRequestException(`No function found for action: ${action}`);
    }

    return await fn(body, { connection: this.connection } as Helpers);
  }
}
