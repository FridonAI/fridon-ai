import { Connection } from '@solana/web3.js';

export abstract class InterfaceSnippet<T extends object, R extends object> {
  constructor(readonly connection: Connection) {}

  abstract execute(data: T): Promise<R>;
}
