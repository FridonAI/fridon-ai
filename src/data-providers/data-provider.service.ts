import { BadRequestException, Injectable } from '@nestjs/common';
import { Connection } from '@solana/web3.js';
import { InterfaceSnippet } from './actions/interface';
import { GetBlockHash } from './actions/get-blockhash';
import { BlockchainTools } from 'src/blockchain/utils/tools/blockchain-tools';

type BlockchainDataProviderCls = new (connection: Connection, tools: BlockchainTools) => InterfaceSnippet<any, any>;

export type Helpers = {
  connection: Connection;
};

@Injectable()
export class DataProviderService {
  constructor(private connection: Connection, private tools: BlockchainTools) { }
  // async resolve(action: string): Promise<BlockchainDataProviderCls> {
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
    const fns: Record<string, BlockchainDataProviderCls> = {
      'get-blockhash': GetBlockHash,
    };

    const cls = fns[action];
    if (!cls) {
      throw new BadRequestException(`No function found for action: ${action}`);
    }

    const instance = new cls(this.connection, this.tools);

    return await instance.execute(body);
  }
}
