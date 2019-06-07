
function d3Chart(dataset, mbars, chart_domain) {

    var w = 800;                        //width
    var h = 500;                        //height
    var padding = {top: 40, right: 40, bottom: 40, left:40};
    var stack = d3.layout.stack();
    var color_hash = {
          0 : ["Completed","#1f77b4"],
            1 : ["Approved","#ff7f0e"],
            2 : ["Submitted","#2ca02c"]

    };

    var div = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);

			//Data, stacked
			stack(dataset);
            var xScale = null

            if(chart_domain == 'time'){
                //Set up scales
                var xScale = d3.time.scale()
                    .domain([new Date(dataset[0][0].time),d3.time.month.offset(new Date(dataset[0][dataset[0].length-2].time),1)])
                    .rangeRound([0, w-padding.left-padding.right]);
            }
            if(chart_domain == 'band'){
                //Set up scales
                var xScale = d3.scaleBand()
                    .domain(data.map(d => d.name))
                    .range([margin.left, width - margin.right])
                    .padding(0.1)
            }


			var yScale = d3.scale.linear()
				.domain([0,
					d3.max(dataset, function(d) {
						return d3.max(d, function(d) {
							return d.y0 + d.y;
						});
					})
				])
				.range([h-padding.bottom-padding.top,0]);

			var xAxis = d3.svg.axis()
						   .scale(xScale)
						   .orient("bottom")
						   .ticks(d3.time.months,1);

			var yAxis = d3.svg.axis()
						   .scale(yScale)
						   .orient("left")
						   .ticks(10);

			//Easy colors accessible via a 10-step ordinal scale
			var colors = d3.scale.category10();

			//Create SVG element
			var svg = d3.select(mbars)
						.append("svg")
						.attr("width", w)
						.attr("height", h);

			// Add a group for each row of data
			var groups = svg.selectAll("g")
				.data(dataset)
				.enter()
				.append("g")
				.attr("class","rgroups")
				.attr("transform","translate("+ padding.left + "," + (h - padding.bottom) +")")
				.style("fill", function(d, i) {
					return color_hash[dataset.indexOf(d)][1];
				});

			// Add a rect for each data value
			var rects = groups.selectAll("rect")
				.data(function(d) { return d; })
				.enter()
				.append("rect")
				.attr("width", 2)
        .on("mouseover", function(d) {
            div.transition()
                .duration(200)
                .style("opacity", .9);
            div	.html(d.y+" "+d.type+" - "+d.x)
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
            })
        .on("mouseout", function(d) {
            div.transition()
                .duration(500)
                .style("opacity", 0);
        })
				.style("fill-opacity",1e-6);


			rects.transition()
			     .duration(function(d,i){
			    	 return 500 * i;
			     })
			     .ease("linear")
			    .attr("x", function(d) {
					return xScale(new Date(d.time));
				})
				.attr("y", function(d) {
					return -(- yScale(d.y0) - yScale(d.y) + (h - padding.top - padding.bottom)*2);
				})
				.attr("height", function(d) {
					return -yScale(d.y) + (h - padding.top - padding.bottom);
				})
				.attr("width", 15)
				.style("fill-opacity",1);

				svg.append("g")
					.attr("class","x axis")
					.attr("transform","translate(40," + (h - padding.bottom) + ")")
					.call(xAxis);


				svg.append("g")
					.attr("class","y axis")
					.attr("transform","translate(" + padding.left + "," + padding.top + ")")
					.call(yAxis);

				// adding legend

				var legend = svg.append("g")
								.attr("class","legend")
								.attr("x", w - padding.right - 65)
								.attr("y", 25)
								.attr("height", 100)
								.attr("width",100);

				legend.selectAll("g").data(dataset)
					  .enter()
					  .append('g')
					  .each(function(d,i){
					  	var g = d3.select(this);
					  	g.append("rect")
					  		.attr("x", w - padding.right - 65)
					  		.attr("y", i*25 + 10)
					  		.attr("width", 10)
					  		.attr("height",10)
					  		.style("fill",color_hash[String(i)][1]);

					  	g.append("text")
					  	 .attr("x", w - padding.right - 50)
					  	 .attr("y", i*25 + 20)
					  	 .attr("height",30)
					  	 .attr("width",100)
					  	 .style("fill",color_hash[String(i)][1])
					  	 .text(color_hash[String(i)][0]);
					  });

				svg.append("text")
				.attr("transform","rotate(-90)")
				.attr("y", 0 - 5)
				.attr("x", 0-(h/2))
				.attr("dy","1em")
				.text("Number");

			svg.append("text")
			   .attr("class","xtext")
			   .attr("x",w/2 - padding.left)
			   .attr("y",h - 5)
			   .attr("text-anchor","middle")
			   .text("Months");

			svg.append("text")
	        .attr("class","title")
	        .attr("x", (w / 2))
	        .attr("y", 20)
	        .attr("text-anchor", "middle")
	        .style("font-size", "16px")
	        .style("text-decoration", "underline")
	        .text("# of programmatic visits per month.");

}
