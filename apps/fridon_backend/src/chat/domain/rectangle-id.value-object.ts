export class RectangleId {
  constructor(private readonly rectangleId: string) {
    if (!rectangleId) {
      throw new BadRequestException(`RectangleId[${rectangleId}] should not be empty`);
    }
  }

  get value(): string {
    return this.rectangleId;
  }
}
