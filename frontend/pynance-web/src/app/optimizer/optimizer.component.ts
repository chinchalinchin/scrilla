import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-optimizer',
  templateUrl: './optimizer.component.html'
})
export class OptimizerComponent implements OnInit {

  private optimizeDisabled : boolean = false;
  private clearDisabled : boolean = true;

  @Input() private explanationDisabled;

  constructor() { }

  ngOnInit() {
  }

}
