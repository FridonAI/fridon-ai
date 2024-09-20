import { Request } from '@nestjs/common';
import { InterfaceSnippet } from './interface';
import { Registry } from '../registry';

type Request = object;

type Response = {
  blockhash: string;
};

@Registry('get-block-hash')
export class GetBlockHash extends InterfaceSnippet<Request, Response> {
  async execute(data: Request): Promise<Response> {
    console.log('data', data);

    return {
      blockhash: (await this.connection.getRecentBlockhash()).blockhash,
    };
  }
}
