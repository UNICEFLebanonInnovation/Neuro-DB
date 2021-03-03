
function d3ChartPie(data, mchart, domain, range, width, height){

    var svg = d3.select(mchart)
        .append("svg")
        .append("g")

    svg.append("g")
        .attr("class", "slices");
    svg.append("g")
        .attr("class", "labels");
    svg.append("g")
        .attr("class", "lines");

    var width = width,
        height = height,
        radius = Math.min(width, height) / 2;
    var padding = {top: 40, right: 40, bottom: 40, left:40};

    var pie = d3.layout.pie()
        .sort(null)
        .value(function(d) {
            return d.value;
        });

    var arc = d3.svg.arc()
        .outerRadius(radius * 0.8)
        .innerRadius(radius * 0.4);

    var outerArc = d3.svg.arc()
        .innerRadius(radius * 0.9)
        .outerRadius(radius * 0.9);

    svg.attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

    var key = function(d){ return d.data.label; };

    var color = d3.scale.ordinal()
        .domain(domain)
        .range(range);

    change(data);

    d3.select(".randomize")
        .on("click", function(){
            change(randomData());
        });


    function change(data) {

        /* ------- PIE SLICES -------*/
        var slice = svg.select(".slices").selectAll("path.slice")
            .data(pie(data), key);

        slice.enter()
            .insert("path")
            .style("fill", function(d) { return color(d.data.label); })
            .attr("class", "slice");

        slice
            .transition().duration(1000)
            .attrTween("d", function(d) {
                this._current = this._current || d;
                var interpolate = d3.interpolate(this._current, d);
                this._current = interpolate(0);
                return function(t) {
                    return arc(interpolate(t));
                };
            })

        slice.exit()
            .remove();

        /* ------- TEXT LABELS -------*/

        var text = svg.select(".labels").selectAll("text")
            .data(pie(data), key);

        text.enter()
            .append("text")
            .attr("dy", ".35em")
            .text(function(d) {
                return d.data.value;
            });

        function midAngle(d){
            return d.startAngle + (d.endAngle - d.startAngle)/2;
        }

        text.transition().duration(1000)
            .attrTween("transform", function(d) {
                this._current = this._current || d;
                var interpolate = d3.interpolate(this._current, d);
                this._current = interpolate(0);
                return function(t) {
                    var d2 = interpolate(t);
                    var pos = outerArc.centroid(d2);
                    pos[0] = radius * (midAngle(d2) < Math.PI ? 1 : -1);
                    return "translate("+ pos +")";
                };
            })
            .styleTween("text-anchor", function(d){
                this._current = this._current || d;
                var interpolate = d3.interpolate(this._current, d);
                this._current = interpolate(0);
                return function(t) {
                    var d2 = interpolate(t);
                    return midAngle(d2) < Math.PI ? "start":"end";
                };
            });

        text.exit()
            .remove();

        /* ------- SLICE TO TEXT POLYLINES -------*/

        var polyline = svg.select(".lines").selectAll("polyline")
            .data(pie(data), key);

        polyline.enter()
            .append("polyline");

        polyline.transition().duration(1000)
            .attrTween("points", function(d){
                this._current = this._current || d;
                var interpolate = d3.interpolate(this._current, d);
                this._current = interpolate(0);
                return function(t) {
                    var d2 = interpolate(t);
                    var pos = outerArc.centroid(d2);
                    pos[0] = radius * 0.95 * (midAngle(d2) < Math.PI ? 1 : -1);
                    return [arc.centroid(d2), outerArc.centroid(d2), pos];
                };
            });

        polyline.exit()
            .remove();

        var legend = svg.append("g")
                        .attr("class","legend")
                        .attr("x", width - padding.right - 65)
                        .attr("y", 35)
                        .attr("height", 120)
                        .attr("width",120);

        legend.selectAll("g").data(data)
              .enter()
              .append('g')
              .each(function(d,i){
                var g = d3.select(this);
                g.append("rect")
                    .attr("x", width - padding.right - 65)
                    .attr("y", i*15 - 50)
                    .attr("width", 10)
                    .attr("height",10)
                    .style("fill",range[String(i)]);

                g.append("text")
                 .attr("x", width - padding.right - 50)
                 .attr("y", i*15 - 40)
                 .attr("height",30)
                 .attr("width",100)
                 .style("fill",range[String(i)])
                 .text(domain[String(i)]);
              });

    };

}

function d3ChartBar(dataset, mbars, chart_domain, domain, range) {

    var w = 800;                        //width
    var h = 500;                        //height
    var padding = {top: 40, right: 40, bottom: 40, left:40},
    width = 960 - padding.left - padding.right,
    height = 500 - padding.top - padding.bottom;
    var stack = d3.layout.stack();

    var div = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);

			//Data, stacked
			stack(dataset);
            var xScale = null

            var xScale = d3.scale.ordinal()
                .domain(domain)
                .range(range)
//                .rangeRoundBands([0, domain.length * 100], .2);
                .rangeRoundBands([0, w-padding.left-padding.right], .2);

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
                           .orient("bottom");

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
					return range[String(i)];
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
                    return xScale(d.name);
				})
				.attr("y", function(d) {
					return -(- yScale(d.y0) - yScale(d.y) + (h - padding.top - padding.bottom)*2);
				})
				.attr("height", function(d) {
					return -yScale(d.y) + (h - padding.top - padding.bottom);
				})
				.attr("width", 30)
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
								.attr("height", 120)
								.attr("width",120);

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
					  		.style("fill",range[String(i)]);

					  	g.append("text")
					  	 .attr("x", w - padding.right - 50)
					  	 .attr("y", i*25 + 20)
					  	 .attr("height",30)
					  	 .attr("width",100)
					  	 .style("fill",range[String(i)])
					  	 .text(chart_domain[String(i)]);
					  });

//			    var texts = svg.selectAll("g.tick")
//			                .each(function(d,i){
//			                    var g = d3.select(this);
//			                    g.attr("transform","translate(" + padding.left * (i+1) + ", 0")");
//			    });

//				svg.append("text")
//				.attr("transform","rotate(-90)")
//				.attr("y", 0 - 5)
//				.attr("x", 0-(h/2))
//				.attr("dy","1em")
//				.text("Number");

//			svg.append("text")
//			   .attr("class","xtext")
//			   .attr("x",w/2 - padding.left)
//			   .attr("y",h - 5)
//			   .attr("text-anchor","middle")
//			   .text("Partners");

//			svg.append("text")
//	        .attr("class","title")
//	        .attr("x", (w / 2))
//	        .attr("y", 20)
//	        .attr("text-anchor", "middle")
//	        .style("font-size", "16px")
//	        .style("text-decoration", "underline")
//	        .text("Disa");

}
