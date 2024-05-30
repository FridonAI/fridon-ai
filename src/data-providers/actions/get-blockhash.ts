import { Request } from "@nestjs/common";
import { InterfaceSnippet } from "./interface";

type Request = object;

type Response = {
  blockhash: string;
};

export class GetBlockHash extends InterfaceSnippet<Request, Response> {
  async execute(data: Request): Promise<Response> {
    console.log('data', data);

    return {
      blockhash: (await this.connection.getRecentBlockhash()).blockhash
    };
  }
}
