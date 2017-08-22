$(function(){
	var bannerNum = $(".index-head-banner ul li").length;
        $(".index-head-banner").css("width", "100%");
	$(".index-head-banner ul").css("width", bannerNum*100+"%");
	var li_width = Math.floor(10000/bannerNum)/100;
	$(".index-head-banner ul li").css( "width",  li_width + "%" );
        $(window).bind('resize',function(){
            var bannerNum = $(".index-head-banner ul li").length;
            $(".index-head-banner").css("width", "100%");
            $(".index-head-banner ul").css("width", bannerNum*100+"%");
            var li_width = Math.floor(10000/bannerNum)/100;
            $(".index-head-banner ul li").css( "width",  li_width + "%" );
        });
        var timer1 = setTimeout(function(){
            clearTimeout(timer1);
            var timer2;
            interval();
            function interval(){
                timer2 = setInterval(function(){
                    $('.index-head-banner li').eq(0).clone(true).appendTo($('.index-head-banner ul'));
                    var classs = $('.index-head-banner li').eq(0).attr('class'),
                        orderArr = classs.match(/[0-9]*$/),
                        orderNum = 1;
                    orderArr && (orderNum += +orderArr[0]);
                    orderNum > bannerNum ? orderNum = 1 : orderNum;
                    orderNum && $('.dot'+orderNum).addClass('active').siblings().removeClass('active');
                    $('.index-head-banner ul').animate({'left':'-100%'},800,function(){
                        $('.index-head-banner li').eq(0).remove();
                        $('.index-head-banner ul').css('left','0');
                    });
                },5000);
            }
            $('.dots').on('click','.dot',function(){
                $(this).addClass('active').siblings().removeClass('active');
                var o = $(this).index()+1;
                var od = $('.index-head-banner ul li').index($('.banner-'+o));
                var cloneArr = [];

                $('.index-head-banner ul').animate({'left':'-'+100*od+'%'},800,function(){
                    for(var i = 0;i < od;i++){
                        cloneArr.push($('.index-head-banner ul li').eq(i).clone(true));
                    }
                    for(var i = 0;i < od;i++){
                        $('.index-head-banner ul li').eq(0).remove();
                    }
                    $('.index-head-banner ul').css('left','0');
                    for(var i in cloneArr){
                        cloneArr[i].appendTo($('.index-head-banner ul'));
                    }
                });
            });
            $('.dots').hover(function(){
                clearTimeout(timer2);
            },function(){
                interval();
            });
        },1000);
       
});