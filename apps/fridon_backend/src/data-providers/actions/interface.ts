import { Connection } from '@solana/web3.js';
import { TokenProgramInstructionFactory } from 'src/blockchain/factories/token-program-instruction-factory';
import { TokenProgramTransactionFactory } from 'src/blockchain/factories/token-program-transaction-factory';
import { TransactionFactory } from 'src/blockchain/factories/transaction-factory';
import { KaminoFactory } from 'src/blockchain/providers/kamino-factory';
import { PointsFactory } from 'src/blockchain/providers/points-factory';
import { SymmetryApiFactory } from 'src/blockchain/providers/symmetry-api-factory';
import { WalletFactory } from 'src/blockchain/providers/wallet-factory';
import { BlockchainTools } from 'src/blockchain/utils/tools/blockchain-tools';

export abstract class InterfaceSnippet<T extends object, R extends object> {
  constructor(
    readonly connection: Connection,
    readonly tools: BlockchainTools,
    readonly tokenProgramInstructionFactory: TokenProgramInstructionFactory,
    readonly tokenProgramTransactionFactory: TokenProgramTransactionFactory,
    readonly transactionFactory: TransactionFactory,
    readonly kaminoFactory: KaminoFactory,
    readonly walletFactory: WalletFactory,
    readonly symmetryFactory: SymmetryApiFactory,
    readonly pointsFactory: PointsFactory,
  ) {}

  abstract execute(data: T): Promise<R>;
}
