import { Connection, PublicKey, PublicKeyInitData } from '@solana/web3.js';
import { getAssociatedTokenAddress } from '@solana/spl-token';

export const connection = new Connection(
  'https://defiland-defiland-634e.mainnet.rpcpool.com/d396f84d-a693-47f8-b3c0-3d7f72bc83e3',
);

export async function findAssociatedTokenAddress(
  walletAddress: PublicKeyInitData,
  tokenMintAddress: PublicKeyInitData,
) {
  return await getAssociatedTokenAddress(
    new PublicKey(tokenMintAddress),
    new PublicKey(walletAddress),
  );
}

export async function getLatestBlockHash() {
  return connection.getLatestBlockhash();
}
