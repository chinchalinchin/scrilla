import { Component, Input, OnInit, SimpleChanges } from '@angular/core';
import { Holding } from 'src/app/models/holding';

const mockPortfolio : Holding[] = [
  { ticker: 'ALLY', allocation: 0.2 },
  { ticker: 'BX', allocation: 0.25 },
  { ticker: 'SNE', allocation: 0.4 },
  { ticker: 'PFE', allocation: 0.1 },
  { ticker: 'TWTR', allocation: 0.05 }
]

@Component({
  selector: 'app-portfolio',
  templateUrl: './portfolio.component.html'
})
export class PortfolioComponent implements OnInit {

  private clearDisabled : boolean = false;
  private portfolio : Holding[] = mockPortfolio
  
  @Input()
  private allocations: number[]


  displayedColumns: string[] = ['ticker', 'allocation'];

  constructor() { }

  ngOnInit() {
  } 

  
  ngOnChanges(changes: SimpleChanges) {
    if (changes.allocations) {
        if(changes.allocations.currentValue.length == 0){ 
          this.displayedColumns = ['ticker']
        }
        else{
          this.displayedColumns = ['ticker', 'allocation']
        }
    }
  }
  
  public getDisplayColumns(){
    for(let holding of this.portfolio){

    }
  }

  public setAllocations(allocations : number[]){
    for(let portion of allocations){
      let thisIndex : number = allocations.indexOf(portion)
      this.portfolio[thisIndex].allocation = portion
    }
  }

}
