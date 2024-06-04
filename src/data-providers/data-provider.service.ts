import { BadRequestException, Injectable, Logger } from '@nestjs/common';
import { Connection } from '@solana/web3.js';
import { BlockchainTools } from 'src/blockchain/utils/tools/blockchain-tools';
import { TokenProgramInstructionFactory } from 'src/blockchain/factories/token-program-instruction-factory';
import { TransactionFactory } from 'src/blockchain/factories/transaction-factory';
import { TokenProgramTransactionFactory } from 'src/blockchain/factories/token-program-transaction-factory';
import { KaminoFactory } from 'src/blockchain/providers/kamino-factory';
import { WalletFactory } from 'src/blockchain/providers/wallet-factory';
import { SymmetryApiFactory } from 'src/blockchain/providers/symmetry-api-factory';
import { PointsFactory } from 'src/blockchain/providers/points-factory';
import { RegistryService } from './registry';

@Injectable()
export class DataProviderService {
  private logger = new Logger(DataProviderService.name);

  constructor(
    private connection: Connection,
    private registryService: RegistryService,
    private readonly tools: BlockchainTools,
    private readonly transactionFactory: TransactionFactory,
    private readonly tokenProgramInstructionFactory: TokenProgramInstructionFactory,
    private readonly tokenProgramTransactionFactory: TokenProgramTransactionFactory,
    private readonly kaminoFactory: KaminoFactory,
    private readonly walletFactory: WalletFactory,
    private readonly pointsFactory: PointsFactory,
    private readonly symmetryFactory: SymmetryApiFactory,
  ) {}

  async resolve(action: string, body: object): Promise<object> {
    this.logger.log(`Resolving action: ${action}`);

    const cls = this.registryService.resolve(action);

    if (!cls) {
      throw new BadRequestException(`No function found for action: ${action}`);
    }

    const instance = new cls(
      this.connection,
      this.tools,
      this.tokenProgramInstructionFactory,
      this.tokenProgramTransactionFactory,
      this.transactionFactory,
      this.kaminoFactory,
      this.walletFactory,
      this.symmetryFactory,
      this.pointsFactory,
    );

    this.logger.log(`Executing action: ${action}`);
    return await instance.execute(body);
  }
}
