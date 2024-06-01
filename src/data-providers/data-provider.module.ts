import { Module } from '@nestjs/common';
import { DataProviderController } from './data-provider.controller';
import { DataProviderService } from './data-provider.service';
import { RegistryService } from './registry';
import { DiscoveryModule } from '@nestjs/core';
import { TransferTokens } from './actions/wallet/transfer-tokens';
import { KaminoBalance } from './actions/kamino/balance';
import { KaminoBorrow } from './actions/kamino/borrow';
import { KaminoPoints } from './actions/kamino/points';
import { KaminoRepay } from './actions/kamino/repay';
import { KaminoSupply } from './actions/kamino/supply';
import { KaminoWithdraw } from './actions/kamino/withdraw';
import { SwapTokens } from './actions/swap/swap';
import { SymmetryBalance } from './actions/symmetry/balance';
import { SymmetryPoints } from './actions/symmetry/points';
import { WalletBalance } from './actions/wallet/wallet-balance';

@Module({
  imports: [DiscoveryModule],
  providers: [
    DataProviderService,
    RegistryService,
    TransferTokens,
    KaminoBalance,
    KaminoBorrow,
    KaminoPoints,
    KaminoRepay,
    KaminoSupply,
    KaminoWithdraw,
    SwapTokens,
    SymmetryBalance,
    SymmetryPoints,
    WalletBalance,
  ],
  controllers: [DataProviderController],
})
export class DataProviderModule {}
