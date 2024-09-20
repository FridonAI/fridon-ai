import { Injectable, OnModuleInit, SetMetadata } from '@nestjs/common';
import { Connection } from '@solana/web3.js';
import { InterfaceSnippet } from './actions/interface';
import { DiscoveryService } from '@nestjs/core';
import { BlockchainTools } from 'src/blockchain/utils/tools/blockchain-tools';
import { TokenProgramInstructionFactory } from 'src/blockchain/factories/token-program-instruction-factory';
import { TransactionFactory } from 'src/blockchain/factories/transaction-factory';
import { TokenProgramTransactionFactory } from 'src/blockchain/factories/token-program-transaction-factory';
import { KaminoFactory } from 'src/blockchain/providers/kamino-factory';
import { WalletFactory } from 'src/blockchain/providers/wallet-factory';
import { SymmetryApiFactory } from 'src/blockchain/providers/symmetry-api-factory';
import { PointsFactory } from 'src/blockchain/providers/points-factory';

const REGISTRY_METADATA_KEY = Symbol('__registry__');

type BlockchainDataProviderCls = new (
  connection: Connection,
  tools: BlockchainTools,
  tokenProgramInstructionFactory: TokenProgramInstructionFactory,
  tokenProgramTransactionFactory: TokenProgramTransactionFactory,
  transactionFactory: TransactionFactory,
  kaminoFactory: KaminoFactory,
  walletFactory: WalletFactory,
  symmetryFactory: SymmetryApiFactory,
  pointsFactory: PointsFactory,
) => InterfaceSnippet<any, any>;

export const Registry = (actionName: string) => {
  return SetMetadata(REGISTRY_METADATA_KEY, actionName);
};

type InstanceWrapper = {
  metatype: unknown;
  name: string;
  instance: unknown;
};

@Injectable()
export class RegistryService implements OnModuleInit {
  private providers: Record<string, unknown> = {};

  constructor(private readonly discoveryService: DiscoveryService) {}

  onModuleInit(): void {
    this.providers = this.scanDiscoverableInstanceWrappers(
      this.discoveryService.getProviders(),
    );
  }

  resolve(action: string): BlockchainDataProviderCls | undefined {
    return this.providers[action] as BlockchainDataProviderCls;
  }

  private scanDiscoverableInstanceWrappers(wrappers: InstanceWrapper[]) {
    return wrappers
      .filter(({ metatype }) => metatype && this.getMetadata(metatype))
      .reduce((acc, { metatype }) => {
        return {
          ...acc,
          [this.getMetadata(metatype)]: metatype,
        };
      }, {});
  }

  private getMetadata(metatype: unknown) {
    return Reflect.getMetadata(REGISTRY_METADATA_KEY, metatype);
  }
}
