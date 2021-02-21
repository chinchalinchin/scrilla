import { Component, Input, OnInit } from '@angular/core';
import { PortfolioComponent } from 'src/app/input/portfolio/portfolio.component';

@Component({
  selector: 'app-valuation',
  templateUrl: './valuation.component.html'
})
export class ValuationComponent implements OnInit {

  public portfolio : PortfolioComponent;
  public graphDisabled : boolean = false;
  public clearDisabled : boolean = true; 

  @Input()
  public explanationDisabled : boolean = true;

  constructor() { }

  ngOnInit(): void {
  }

  public evaluate(){

  }

  public clear(){
    
  }
}
