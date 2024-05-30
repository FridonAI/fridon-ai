import { Connection } from "@solana/web3.js";
import { BlockchainTools } from "src/blockchain/utils/tools/blockchain-tools";

export abstract class InterfaceSnippet<T extends object, R extends object> {
  constructor(readonly connection: Connection, readonly tools: BlockchainTools) { }

  abstract execute(data: T): Promise<R>;
}