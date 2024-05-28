import { Helpers } from '../data-provider.service';

export default async function getBlockHash(
  data: any,
  providers: Helpers,
): Promise<any> {
  console.log('getBlockHash', data, providers);
  return { message: 'test-getBlockHash', data };
}
