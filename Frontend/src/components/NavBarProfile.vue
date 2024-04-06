<template>
    <header class="sticky-top header">
      <div class="position-relative ms-4 me-4 pb-3">
        <span>
          <router-link to="/dash" v-if="role == 'student'">
            <img src="../assets/logo1.png" alt="Logo" width="110" height="60" class="d-inline-block align-text-top" />
          </router-link>
          <router-link to="/tag" v-else-if="role == 'admin'">
            <img src="../assets/logo1.png" alt="Logo" width="110" height="60" class="d-inline-block align-text-top" />
          </router-link>
        </span>
        <div class="position-absolute top-0 mt-3 end-0" >
            <button @click="logout" style="font-size: large; color: whitesmoke" class="btn btn-danger">
                Logout <i class="bi bi-box-arrow-right"></i>
            </button>
          
        </div>
        <!-- <hr class="border border-primary border-2 opacity-100" /> -->
      </div>
    </header>
  </template>
  <script>
  import router from "@/router";
  export default {
    name: "NavBarProfile",
    data() {
      return {
        role: localStorage.getItem("role")
      }
    },
    props: ["title"],
    methods: {
      logout() {
        localStorage.clear();
        return router.push("/");
      },
    },
  };
  </script>
  <style scoped>
  .header {
    background-color: #6B62FF;
  }
  
  a {
    color: inherit;
    /* color: #653239; */
    text-decoration: none;
  }
  
  form.search {
    display: inline-block;
    position: absolute;
    left: 30%;
    padding-top: .25rem;
    margin-top: .5rem;
    /* margin-left: 25%; */
    /* width: auto; */
  }
  
  input[type='text'].search {
    padding: 1rem;
    width: 40rem;
    height: 3.2rem;
    border-radius: 50px;
    margin-right: -50px;
  }
  </style>