export type BalanceType = {
  symbol: string;
  mintAddress: string;
  amount: string;
  value: string;
  type?: string;
};

export enum BalanceOperationType {
  Borrowed = 'borrow',
  Deposited = 'supply',
  WalletBalance = 'walletBalance',
  Staked = 'stake',
  All = 'all',
}

export enum PointsProviderType {
  Kamino = 'kamino',
  Symmetry = 'symmetry',
  Drift = 'drift',
  All = 'all',
}

export type UserPointsResponseType = {
  walletAddress: string;
  points: number;
  provider: PointsProviderType;
};
