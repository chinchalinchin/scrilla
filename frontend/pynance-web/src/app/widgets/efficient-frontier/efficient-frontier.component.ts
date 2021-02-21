import { Component, Input, OnInit } from '@angular/core';
import { PortfolioComponent } from 'src/app/input/portfolio/portfolio.component';

@Component({
  selector: 'app-efficient-frontier',
  templateUrl: './efficient-frontier.component.html'
})
export class EfficientFrontierComponent implements OnInit {

  public portfolio: PortfolioComponent;
  public frontierDisabled : boolean = false;
  public clearDisabled : boolean = true;

  @Input()
  public explanationDisabled : boolean = true;

  constructor() { }

  ngOnInit(): void {
  }

  public calculate(){

  }

  public clear(){

  }
}
