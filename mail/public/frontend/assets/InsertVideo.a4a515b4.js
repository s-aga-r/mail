import{v as _,a7 as v,D as C,ab as k,U as r,x as u,y as c,M as h,a5 as x,a6 as B,K as a,C as l,F as y,a2 as n,I as U,B as w,J as p,Q as F}from"./frappe-ui.6bb07023.js";const I={name:"InsertImage",props:["editor"],expose:["openDialog"],data(){return{addVideoDialog:{url:"",file:null,show:!1}}},components:{Button:v,Dialog:C,FileUploader:k},methods:{openDialog(){this.addVideoDialog.show=!0},onVideoSelect(i){let o=i.target.files[0];!o||(this.addVideoDialog.file=o)},addVideo(i){this.editor.chain().focus().insertContent(`<video src="${i}"></video>`).run(),this.reset()},reset(){this.addVideoDialog=this.$options.data().addVideoDialog}}},N={class:"flex items-center space-x-2"},S=["src"];function A(i,o,b,L,e,t){const s=r("Button"),V=r("FileUploader"),g=r("Dialog");return u(),c(F,null,[h(i.$slots,"default",x(B({onClick:t.openDialog}))),a(g,{options:{title:"Add Video"},modelValue:e.addVideoDialog.show,"onUpdate:modelValue":o[2]||(o[2]=d=>e.addVideoDialog.show=d),onAfterLeave:t.reset},{"body-content":l(()=>[a(V,{"file-types":"video/*",onSuccess:o[0]||(o[0]=d=>e.addVideoDialog.url=d.file_url)},{default:l(({file:d,progress:f,uploading:m,openFileSelector:D})=>[y("div",N,[a(s,{onClick:D},{default:l(()=>[n(U(m?`Uploading ${f}%`:e.addVideoDialog.url?"Change Video":"Upload Video"),1)]),_:2},1032,["onClick"]),e.addVideoDialog.url?(u(),w(s,{key:0,onClick:()=>{e.addVideoDialog.url=null,e.addVideoDialog.file=null}},{default:l(()=>[n(" Remove ")]),_:2},1032,["onClick"])):p("",!0)])]),_:1}),e.addVideoDialog.url?(u(),c("video",{key:0,src:e.addVideoDialog.url,class:"mt-2 w-full rounded-lg",type:"video/mp4",controls:""},null,8,S)):p("",!0)]),actions:l(()=>[a(s,{variant:"solid",onClick:o[1]||(o[1]=d=>t.addVideo(e.addVideoDialog.url))},{default:l(()=>[n(" Insert Video ")]),_:1}),a(s,{onClick:t.reset},{default:l(()=>[n("Cancel")]),_:1},8,["onClick"])]),_:1},8,["modelValue","onAfterLeave"])],64)}var R=_(I,[["render",A]]);export{R as default};
//# sourceMappingURL=InsertVideo.a4a515b4.js.map
