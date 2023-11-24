#include <tiramisu/tiramisu.h>
#include <tiramisu/auto_scheduler/evaluator.h>
#include <tiramisu/auto_scheduler/search_method.h>
#include "function_syr2k_MEDIUM_wrapper.h"

using namespace tiramisu;


int main(int argc, char **argv)
{
    tiramisu::init("function_syr2k_MEDIUM");

    // -------------------------------------------------------
    // Layer I
    // ------------------------------------------------------- 

    //Iteration variables    
//     var i("i", 0, 240), j("j", 0, 240), k("k", 0, 200);
    var i("i", 0, 240), j("j"), k("k", 0, 200);
    

    //inputs
    input A("A", {i, k}, p_float64);
    input B("B", {i, k}, p_float64);
    input C("C", {i, j}, p_float64);


    //Computations
    computation C_beta("{C_beta[i,j]: 0<=i<240 and 0<=j<=i}", expr(), true, p_float64, global::get_implicit_function());
    C_beta.set_expression(C(i,j)*1.2);
    computation C_out("{C_out[i,k,j]: 0<=i<240 and 0<=j<=i and 0<=k<200}", expr(), true, p_float64, global::get_implicit_function());
    C_out.set_expression(C(i,j)+ A(j, k)*B(i, k)*1.5 + B(j, k)*A(i, k)*1.5);

    
    // -------------------------------------------------------
    // Layer II
    // -------------------------------------------------------
    C_beta.then(C_out, i);

    // -------------------------------------------------------
    // Layer III
    // -------------------------------------------------------
    //Input Buffers
    buffer b_A("b_A", {240,200}, p_float64, a_input);
    buffer b_B("b_B", {240,200}, p_float64, a_input);
    buffer b_C("b_C", {240,240}, p_float64, a_output);
    

    //Store inputs
    A.store_in(&b_A);
    B.store_in(&b_B);
    C.store_in(&b_C);
    

    //Store computations
    C_beta.store_in(&b_C);
    C_out.store_in(&b_C, {i,j});

    // -------------------------------------------------------
    // Code Generation
    // -------------------------------------------------------
    tiramisu::codegen({&b_A, &b_B, &b_C}, "function_syr2k_MEDIUM.o");

    return 0;
}

