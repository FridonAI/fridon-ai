import Replicate from 'replicate';

type ModelResponseSuccess = { vector: [number[]] };

export class ReplicateAdapter {
  private readonly replicate: Replicate = new Replicate({
    auth: process.env['REPLICATE_API_TOKEN']!,
  });

  async getEmbeddings(arr: number[][]): Promise<ModelResponseSuccess> {
    let prediction = await this.replicate.deployments.predictions.create(
      'fridonai',
      'chronos-t5-large',
      {
        input: {
          inputs: arr,
        },
      },
    );
    prediction = await this.replicate.wait(prediction);
    return prediction.output as ModelResponseSuccess;
  }
}
