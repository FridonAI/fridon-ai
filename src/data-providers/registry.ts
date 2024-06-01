import { Injectable, OnModuleInit, SetMetadata } from '@nestjs/common';
import { Connection } from '@solana/web3.js';
import { InterfaceSnippet } from './actions/interface';
import { DiscoveryService } from '@nestjs/core';

const REGISTRY_METADATA_KEY = Symbol('__registry__');

type BlockchainDataProviderCls = new (
  connection: Connection,
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
