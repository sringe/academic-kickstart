+++
# A Projects section created with the Portfolio widget.
widget = "portfolio"  # See https://sourcethemes.com/academic/docs/page-builder/
headless = true  # This file represents a page section.
active = true  # Activate this widget? true/false
weight = 65  # Order that this section will appear.
external_link = true 
title = ""
subtitle = ""

[content]
  # Page type to display. E.g. project.
  page_type = "project"
  # Filter toolbar (optional).
  # Add or remove as many filters (`[[content.filter_button]]` instances) as you like.
  # To show all items, set `tag` to "*".
  # To filter by a specific tag, set `tag` to an existing tag name.
  # To remove toolbar, delete/comment all instances of `[[content.filter_button]]` below.
  
  # Default filter index (e.g. 0 corresponds to the first `[[filter_button]]` instance below).
  filter_default = 0
  
  # [[content.filter_button]]
  #   name = "All"
  #   tag = "*"
  
  # [[content.filter_button]]
  #   name = "Deep Learning"
  #   tag = "Deep Learning"
  
  # [[content.filter_button]]
  #   name = "Other"
  #   tag = "Demo"

[design]
  # Choose how many columns the section has. Valid values: 1 or 2.
  columns = "1"

  # Toggle between the various page layout types.
  #   1 = List
  #   2 = Compact
  #   3 = Card
  #   5 = Showcase
  view = 5

  # For Showcase view, flip alternate rows?
  flip_alt_rows = true

[design.background]
  # Apply a background color, gradient, or image.
  #   Uncomment (by removing `#`) an option to apply it.
  #   Choose a light or dark text color by setting `text_color_light`.
  #   Any HTML color name or Hex value is valid.
  
  # Background color.
  # color = "navy"
  
  # Background gradient.
  # gradient_start = "DeepSkyBlue"
  # gradient_end = "SkyBlue"
  
  # Background image.
  # image = "background.jpg"  # Name of image in `static/img/`.
  # image_darken = 0.6  # Darken the image? Range 0-1 where 0 is transparent and 1 is opaque.

  # Text color (true=light or false=dark).
  # text_color_light = true  
  
[advanced]
 # Custom CSS. 
 css_style = ""
 
 # CSS class.
 css_class = ""
+++


<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
img {
  display: block;
  margin-left: auto;
  margin-right: auto;
}
</style>
</head>

<!--
<a href="../project_general/generalresearchgoals/" style="color: black">
</a>
width=75% class="center" alt=""
../project/SolvationAndElectrifiedInterfaces/
-->
<img src="featured.png" usemap="#image-map" width="75%" class="center">
<map name="image-map">
    <area href="../project/materialscreening/" alt="material screening" title="material screening" coords="10,300,240,590" shape="rect">
    <area href="../project/solvationandelectrifiedinterfaces/" alt="solvation &amp; electrified interfaces" title="solvation &amp; electrified interfaces" coords="250,300,550,590" shape="rect">
    <area href="../project/multiscalemodeling/" alt="kinetics &amp; mass transport" title="kinetics &amp; mass transport" coords="560,300,800,590" shape="rect">
</map>

<br>
<ul>
  <li> Our world today is facing an unprecedented environmental challenge, with the energy demand steadily increasing, the CO<sub>2</sub> concentration in the atmosphere reaching record-high levels in the human history, and oil, gas and coal being estimated to last for around 50--100 years. Renewable electric energy from solar cells is now available on a cost-efficient level, and the carbon-neutral conversion of this electric energy and its storage has now risen to be the most significant challenge for humanity.
  <li> Electrochemical energy conversion and storage provides in this respect sustainable solutions which are expected to sky-rocket over the next years and become as important as never before to save our planet. Unfortunately, most such processes are not yet industrially competitive, albeit an immense research effort has been made over the last decades. A central role in the future sustainable energy landscape is played by the electrochemical reduction of the greenhouse CO<sub>2</sub> gas (CO<sub>2</sub>R), which offers an environmentally highly valuable route to fuels, but is still not economically feasible due to catalysts exhibiting high overpotentials and poor product selectivity.  At the same time, hydrogen gas, which is essential for the chemical industry, is almost exclusively harvested via carbon-intensive steam reforming. The sustainable alternative, electrochemical water splitting, is again limited by high overpotentials making the process economically intractable. The recent environmental changes have, however, increased the political and economic momentum towards carbon-neutral harvesting and conversion of energy.
  <li> In the age of computing, simulations based on quantum chemistry have become an indispensible and highly promising tool to approach this global problem. With the rise of machine learning, quantum chemistry is expected to become even more essential to understand electrochemical processes and the structure of materials, or to perform high-throughput screening of energy materials approaching the gigantic chemical search space that only computational science can handle.
  <li> Our group is working at the front of computational energy science following essentially two paths. On the one hand, we are working on both the fundamental side and try to understand energy conversion and storage on the microscopic and multi-scale. This will provide new insights about the physics and chemistry of such processes which will increase our understanding and help us to develop novel solutions with unprecedented performance. On the other hand, we try to screen catalyst and electrode materials from the chemical design space to develop highly optimized materials for energy science. For both paths, we work also closely together with many great experimentalists, at many leading universities in Korea, Europe and America! We welcome any interested student to follow us on this exciting path and persue a successful career in computational energy science!
</ul>

<!--
<figcaption><a href="../project_general/generalresearchgoals/" style="color: rgb(0,0,0)"><p style="font-size: 1.6rem"><b>General research interest</b></p></a><p style="font-size: 1.0rem">First-principles, multi-scale computational modeling for energy conversion and storage.</p></figcaption>
-->
<!--
{{ $do_link := true }}
{{if $do_link}}<a href="{{ $link }}" {{ $target | safeHTMLAttr }}>{{end}}
  <img src="{{ $image.RelPermalink }}" alt="">
{{if $do_link}}</a>{{end}}
<img src="featured.png" alt>
</a>
<a href="project/GeneralResearchGoals/">
<div class="col-12 col-md-3 order-first {{$order}}">
  {{ $resource := ($item.Resources.ByType "image").GetMatch "*featured*" }}
  {{ with $resource }}
  {{ $resource := 
  {{ $image := .Resize "540x" }}
  {{if $do_link}}<a href="{{ $link }}" {{ $target | safeHTMLAttr }}>{{end}}
    <img src="{{ $image.RelPermalink }}" alt="">
  {{if $do_link}}</a>{{end}}
  {{end}}
</div>
-->
<hr>
