import { PublicKey } from '@metaplex-foundation/js';
import { Connection, PublicKeyInitData } from '@solana/web3.js';
import { getAssociatedTokenAddress } from 'spl';

export async function findAssociatedTokenAddress(
  walletAddress: PublicKeyInitData,
  tokenMintAddress: PublicKeyInitData,
) {
  return await getAssociatedTokenAddress(
    new PublicKey(tokenMintAddress),
    new PublicKey(walletAddress),
  );
}

export async function getLatestBlockHash(connection: Connection) {
  return connection.getLatestBlockhash();
}
